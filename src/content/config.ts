import { defineCollection, z } from 'astro:content';

const overview = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
  }),
});

const taxonomies = defineCollection({
  type: 'content', 
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    taxonomy: z.string().optional(),
  }),
});

const entries = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    taxonomy: z.string().optional(),
    taxonomyContext: z.string().optional(),
  }),
});

export const collections = {
  overview,
  taxonomies,
  entries,
};